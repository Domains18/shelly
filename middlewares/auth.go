package middlewares

import (
	"github.com/Domains18/SchoolIt/auth"
	"github.com/gin-gonic/gin"
)

func Auth() gin.HandlerFunc{
	return func(context *gin.Context) {
		tokenString := context.GetHeader("Authorization")
		if tokenString == ""{
			context.JSON(401, gin.H{"error": "token Auth not found"})
			context.Abort()
			return
		}
		err := auth.ValidateTokens(tokenString)
		if err != nil {
			context.JSON(401, gin.H{"errror": err.Error()})
			context.Abort()
			return
		}
		context.Next()
	}
}