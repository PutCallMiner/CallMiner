package handlers

import (
	"net/http"

	"github.com/a-h/templ"
	"github.com/go-chi/chi/v5"

	"github.com/PutCallMiner/CallMiner/views"
)

type DashboardHandler struct{}

func NewDashboardHandler() *DashboardHandler {
	return &DashboardHandler{}
}

func (h *DashboardHandler) get(w http.ResponseWriter, r *http.Request) {
	templ.Handler(views.Page(nil, "/", "Dashboard", "")).ServeHTTP(w, r)
}

func (h *DashboardHandler) Register() chi.Router {
	r := chi.NewRouter()

	r.Get("/", h.get)

	return r
}
