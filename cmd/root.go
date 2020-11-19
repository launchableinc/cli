package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// RootCmd is root command
var RootCmd = &cobra.Command{
	Use:   "record",
	Short: "command line calculator",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("root command")
	},
}
