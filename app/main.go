package main

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/go-chi/chi/v5"

	"github.com/PutCallMiner/CallMiner/handlers"
	"github.com/PutCallMiner/CallMiner/views"
)

var navLinks = []views.NavLink{
	{URL: "/", Title: "Dashboard", Description: "View call data and statistics"},
	{URL: "/transcripts", Title: "Transcripts", Description: "View call transcripts"},
}

func main() {
	r := chi.NewRouter()

	r.Get("/public/*", serveStatic)

	r.Mount(navLinks[0].URL, handlers.NewDashboardHandler(0, navLinks).Register())
	r.Mount(navLinks[1].URL, handlers.NewTranscriptHandler(1, navLinks).Register())

	fmt.Println("Server is starting on port 3000...")
	err := http.ListenAndServe(":3000", r)
	if err != nil {
		panic(err)
	}
}

func serveStatic(w http.ResponseWriter, r *http.Request) {
	rctx := chi.RouteContext(r.Context())
	pathPrefix := strings.TrimSuffix(rctx.RoutePattern(), "/*")
	fs := http.StripPrefix(pathPrefix, http.FileServer(http.Dir("public")))
	fs.ServeHTTP(w, r)
}
