package cmd

import (
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"os/exec"

	_ "github.com/launchableinc/cli/statik"
	"github.com/rakyll/statik/fs"
	"github.com/spf13/cobra"
)

func init() {
	RecordCmd.AddCommand(commitCmd())
}

// CommitCmd creates commit command
func commitCmd() *cobra.Command {
	var source = ""
	cmd := &cobra.Command{
		Use:   "commit",
		Short: "Record commit",
		RunE: func(cmd *cobra.Command, args []string) error {
			if err := runCommit(source); err != nil {
				return err
			}
			return nil
		},
	}
	cmd.Flags().StringVarP(&source, "source", "s", "", "Source directory to read from")

	return cmd
}

// RunCommit runs exe_deploy.jar
func runCommit(source string) error {
	staticFs, err := fs.New()
	if err != nil {
		return err
	}

	file, err := staticFs.Open("/exe_deploy.jar")
	if err != nil {
		return err
	}
	defer file.Close()

	tmpFile, err := ioutil.TempFile("/tmp", "jar")
	if err != nil {
		return err
	}
	defer os.Remove(tmpFile.Name())

	_, err = io.Copy(tmpFile, file)
	if err != nil {
		return err
	}

	var java string
	if _, err := exec.LookPath("java"); err != nil {
		if _, err = exec.LookPath("$JAVA_HOME/bin/java"); err != nil {
			return err
		}
		java = "$JAVA_HOME/bin/java"
	} else {
		java = "java"
	}

	out, err := exec.Command(java, "-jar", tmpFile.Name(), "ingest:commit", source).CombinedOutput()
	if err != nil {
		fmt.Println(string(out))
		return err
	}
	return err
}
