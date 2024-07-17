package handlers

import (
	"net/http"

	"github.com/a-h/templ"
	"github.com/go-chi/chi/v5"

	"github.com/PutCallMiner/CallMiner/views"
)

type TranscriptHandler struct{}

func NewTranscriptHandler() *TranscriptHandler {
	return &TranscriptHandler{}
}

func (h *TranscriptHandler) get(w http.ResponseWriter, r *http.Request) {
	templ.Handler(views.Page(nil, "/transcripts", "Transcripts", "")).ServeHTTP(w, r)
}

func (h *TranscriptHandler) Register() chi.Router {
	r := chi.NewRouter()

	r.Get("/", h.get)

	return r
}
