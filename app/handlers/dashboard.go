package handlers

import (
	"net/http"

	"github.com/a-h/templ"
	"github.com/go-chi/chi/v5"

	"github.com/PutCallMiner/CallMiner/views"
)

type DashboardHandler struct {
	idx      int
	NavLinks []views.NavLink
}

func NewDashboardHandler(idx int, navLinks []views.NavLink) *DashboardHandler {
	return &DashboardHandler{idx, navLinks}
}

func (h *DashboardHandler) get(w http.ResponseWriter, r *http.Request) {
	templ.Handler(views.Page(nil, h.NavLinks, h.idx)).ServeHTTP(w, r)
}

func (h *DashboardHandler) Register() chi.Router {
	r := chi.NewRouter()

	r.Get("/", h.get)

	return r
}
