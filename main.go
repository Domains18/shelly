package main

import (
	"github.com/Domains18/SchoolIt/controllers"
	"github.com/Domains18/SchoolIt/database"
	"github.com/Domains18/SchoolIt/middlewares"
	"github.com/gin-gonic/gin"
)

func main() {
	database.Connect("root:root@tcp(localhost:3306)/jwt_demo?parseTime=true")
	database.Migrate()
	//initialize router
	router := initRouter()
	err :=router.Run(":8000")
	if err !=nil {
		panic("error")
	}
}


func initRouter() *gin.Engine {
	router := gin.Default()
	api := router.Group("/api")
	{
		api.POST("/token", controllers.GenerateToken)
		api.POST("/user/register", controllers.RegisterUser)
		secured := api.Group("/secured").Use(middlewares.Auth())
		{
			secured.GET("/ping", controllers.Ping)
		}
	}
	return router
}