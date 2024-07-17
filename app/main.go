package main

import (
	"fmt"
	"net/http"
	"strings"

	"github.com/go-chi/chi/v5"

	"github.com/PutCallMiner/CallMiner/handlers"
)

func main() {
	r := chi.NewRouter()

	r.Get("/public/*", serveStatic)

	r.Mount("/", handlers.NewDashboardHandler().Register())
	r.Mount("/transcripts", handlers.NewTranscriptHandler().Register())

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
