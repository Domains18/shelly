package database

import (
	"context"
	"fmt"
	"os"

	"github.com/jackc/pgx/v5"
)

func ConnectDatabase() {
	connectionString := os.Getenv("DATABASEuRL")

	conn, err := pgx.Connect(context.Background(), connectionString)
	if err != nil {
		panic(err)
	}

	defer conn.Close(context.Background())


	var version string

	err = conn.QueryRow(context.Background(), "SELECT version()").Scan(&version)

	if err != nil {
		panic(err)
	}


	fmt.Printf("version=%s\n", version)
}