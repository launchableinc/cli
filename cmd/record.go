package cmd

import (
	"github.com/spf13/cobra"
)

// RecordCmd is record command
var RecordCmd = &cobra.Command{
	Use:           "record",
	Short:         "Record your repo data tor Launchable",
	SilenceErrors: true,
	SilenceUsage:  true,
}

func init() {
	RootCmd.AddCommand(RecordCmd)
}
