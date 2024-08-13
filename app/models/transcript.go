package models

import (
	"time"
)

type Transcript struct {
	ID           int
	AgentID      int
	Agent        string
	Timestamp    time.Time
	DurationSecs int
	Score        int
	Topic        string
	Tags         []string
}

var transcripts = []Transcript{
	{1, 1, "Alice", time.Now(), 600, 90, "Extending a loan", []string{"Loan"}},
	{2, 1, "Alice", time.Now(), 1200, 80, "Refinancing a mortgage", []string{"Mortgage"}},
	{3, 2, "Bob", time.Now(), 1800, 70, "Opening a new account", []string{"Account"}},
	{4, 2, "Bob", time.Now(), 2400, 60, "Closing an account", []string{"Account"}},
	{5, 3, "Charlie", time.Now(), 3000, 50, "Applying for a credit card", []string{"Credit Card"}},
	{6, 3, "Charlie", time.Now(), 3600, 40, "Reporting a lost card", []string{"Credit Card"}},
	{7, 3, "David", time.Now(), 200, 30, "Checking a balance", []string{"Account", "Balance"}},
}

type TranscriptService struct{}

func NewTranscriptService() *TranscriptService {
	return &TranscriptService{}
}

func (s *TranscriptService) List() ([]Transcript, error) {
	return transcripts, nil
}
