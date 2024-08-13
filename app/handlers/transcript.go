package handlers

import (
	"net/http"

	"github.com/a-h/templ"

	"github.com/PutCallMiner/CallMiner/models"
	"github.com/PutCallMiner/CallMiner/views"
)

type TranscriptHandler struct {
	idx      int
	service  *models.TranscriptService
	navLinks []views.NavLink
}

func NewTranscriptHandler(idx int, service *models.TranscriptService, navLinks []views.NavLink) *TranscriptHandler {
	return &TranscriptHandler{idx, service, navLinks}
}

func (h TranscriptHandler) get(w http.ResponseWriter, r *http.Request) {
	arr, err := h.service.List()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}

	main := views.Transcripts(arr)
	page := views.Page(main, h.navLinks, h.idx, "transcripts")

	templ.Handler(page).ServeHTTP(w, r)
}

func (h TranscriptHandler) Register() http.Handler {
	r := http.NewServeMux()

	r.HandleFunc("GET /", h.get)

	return r
}
