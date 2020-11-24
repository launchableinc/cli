package cmd

import (
	"fmt"
	"net/http"
	"runtime"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

const Version = "0.2.0"

var cfgFile string

// RootCmd is root command
var RootCmd = &cobra.Command{
	Use:           "cli",
	Short:         "Launchable CLI",
	SilenceErrors: true,
	SilenceUsage:  true,
	Version:       Version,
}

func init() {
	cobra.OnInitialize(initConfig)

	RootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default $HOME/.launchable.yml)")
	RootCmd.PersistentFlags().StringP("url", "", "https://api.mercury.launchableinc.com", "Launchable endpoint URL")

	viper.BindPFlag("url", RootCmd.PersistentFlags().Lookup("url"))
}

func initConfig() {
	if cfgFile != "" {
		viper.SetConfigFile(cfgFile)
	}

	viper.SetConfigName(".launchable")
	viper.AddConfigPath("$HOME")
	viper.AutomaticEnv()

	viper.ReadInConfig()
}

func newDefaultClient() (*Client, error) {
	endpointURL := viper.GetString("url")
	httpClient := &http.Client{}
	userAgent := fmt.Sprintf("Launchable/%s (%s)", Version, runtime.Version())
	return newClient(endpointURL, httpClient, userAgent)
}
