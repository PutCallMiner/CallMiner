package main

import (
	"fmt"
	"net/http"

	"github.com/PutCallMiner/CallMiner/handlers"
	"github.com/PutCallMiner/CallMiner/models"
	"github.com/PutCallMiner/CallMiner/views"
)

var navLinks = []views.NavLink{
	{URL: "", Title: "Dashboard", Description: "View call data and statistics"},
	{URL: "transcripts", Title: "Transcripts", Description: "View call transcripts"},
}

func main() {
	r := http.NewServeMux()
	ts := models.NewTranscriptService()

	r.HandleFunc("GET /public/*", serveStatic)

	r.Handle("GET /", handlers.NewDashboardHandler(0, navLinks).Register())
	r.Handle("GET /transcripts", handlers.NewTranscriptHandler(1, ts, navLinks).Register())

	fmt.Println("Server is starting on port 3000...")
	err := http.ListenAndServe(":3000", r)
	if err != nil {
		panic(err)
	}
}

func serveStatic(w http.ResponseWriter, r *http.Request) {
	fs := http.StripPrefix("/public/", http.FileServer(http.Dir("public")))
	fs.ServeHTTP(w, r)
}
