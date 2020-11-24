package cmd

import (
	"context"
	"errors"
	"os"
	"strings"
	"time"

	"github.com/go-git/go-git"
	"github.com/spf13/cobra"
)

func init() {
	RecordCmd.AddCommand(buildCmd())
}

// BuildCmd creates build command
func buildCmd() *cobra.Command {
	var name string
	var source string
	var withCommit bool
	cmd := &cobra.Command{
		Use:   "build",
		Short: "Record build",
		RunE: func(cmd *cobra.Command, args []string) error {
			if err := runBuild(withCommit, name, source); err != nil {
				return err
			}
			return nil
		},
	}
	cmd.Flags().BoolVarP(&withCommit, "with-commit", "", true, "send commit simaltaniously")
	cmd.Flags().StringVarP(&source, "source", "s", "", "Source directory to read from")
	cmd.Flags().StringVarP(&source, "name", "n", "", "Build Identifier")

	return cmd
}

type repo struct {
	repositoryName string `json: "repositoryName"`
	commitHash     string `json: "commitHash"`
}

type payload struct {
	buildNumber  string `json: "buildNumber"`
	commitHashes []repo `json: "commitHashes"`
}

func runBuild(withCommit bool, name string, source string) error {
	token, org, workspace, err := parseToken()
	if withCommit {
		runCommit(source)
	}

	var repoName string
	var repoPath string
	if s := strings.Split(source, "="); len(s) == 2 {
		repoName = s[0]
		repoPath = s[1]
	} else {
		repoName = source
		repoPath = source
	}

	r, err := git.PlainOpen(repoPath)
	if err != nil {
		return err
	}
	h, err := r.Head()
	if err != nil {
		return err
	}
	repos := append([]repo{}, repo{repoName, h.Hash().String()})

	w, err := r.Worktree()
	if err != nil {
		return err
	}
	submodules, err := w.Submodules()
	if err != nil {
		return err
	}
	for _, s := range submodules {
		submoduleRepos, err := wolkSubmodule(s, repoName)
		if err != nil {
			return err
		}
		repos = append(repos, submoduleRepos...)
	}

	client, err := newDefaultClient()
	ctx, cancel := context.WithTimeout(context.Background(), 120*time.Second)
	defer cancel()

	client.postApi(ctx, token, workspace, org, name, repos)

	return nil
}

func wolkSubmodule(status *git.Submodule, parentName string) ([]repo, error) {
	r, err := git.PlainOpen(status.Config().URL)

	if err != nil {
		return nil, err
	}
	h, err := r.Head()
	if err != nil {
		return nil, err
	}

	w, err := r.Worktree()
	if err != nil {
		return nil, err
	}
	submodules, err := w.Submodules()
	if err != nil {
		return nil, err
	}
	repos := []repo{}
	repos = append(repos, repo{parentName + "/" + status.Config().Name, h.Hash().String()})

	for _, status := range submodules {
		newRepos, err := wolkSubmodule(status, status.Config().Name)
		if err != nil {
			return nil, err
		}
		repos = append(repos, newRepos...)
	}
	return repos, nil
}

func (client *Client) postApi(ctx context.Context, token string, workspace string, organization string, buildNumber string, repos []repo) error {
	path := "intake/organizations/" + workspace + "/workspaces/" + organization + "/builds"
	req, err := client.newRequest(ctx, "POST", path, nil)
	if err != nil {
		return err
	}
	req.Header.Add("Content-Type", "application/json")
	req.Header.Add("Authorization", "Bearer "+token)

	res, err := client.HTTPClient.Do(req)
	print(res.Body)

	if err != nil {
		return err
	}
	return nil
}

func parseToken() (string, string, string, error) {
	token := os.Getenv("LAUNCHABLE_TOKEN")
	s := strings.Split(token, ":")
	if len(s) != 3 {
		return "", "", "", errors.New("Please set LAUNCHABLE_TOKEN environment variable to the Launchable API token")
	}
	user := s[1]
	s = strings.Split(user, "/")

	return token, s[0], s[1], nil
}
