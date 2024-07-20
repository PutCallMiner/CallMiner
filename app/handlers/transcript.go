package handlers

import (
	"net/http"

	"github.com/a-h/templ"
	"github.com/go-chi/chi/v5"

	"github.com/PutCallMiner/CallMiner/views"
)

type TranscriptHandler struct {
	idx      int
	NavLinks []views.NavLink
}

func NewTranscriptHandler(idx int, navLinks []views.NavLink) *TranscriptHandler {
	return &TranscriptHandler{idx, navLinks}
}

func (h *TranscriptHandler) get(w http.ResponseWriter, r *http.Request) {
	templ.Handler(views.Page(nil, h.NavLinks, h.idx)).ServeHTTP(w, r)
}

func (h *TranscriptHandler) Register() chi.Router {
	r := chi.NewRouter()

	r.Get("/", h.get)

	return r
}
