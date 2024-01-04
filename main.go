package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, req *http.Request) {
		if req.Header.Get("Accept") == "text/html" {
			http.ServeFile(w, req, "./public/index.html")
		} else if req.Header.Get("Accept") == "application/json" {
			w.Header().Set("Content-Type", "application/json")
			w.Write([]byte(`{"message": "This is the Api"}`))
		} else {
			w.Write([]byte("This is the API"))

		}
	})

	port := os.Getenv("PORT ")
	if port == "" {
		port = "5000"
	}
	fmt.Println("server is running on port: " + port)
	err := http.ListenAndServe(":"+port, nil)
	if err != nil {
		return
	}
}
