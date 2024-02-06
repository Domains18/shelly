package auth

import (
	"errors"
	"github.com/dgrijalva/jwt-go"
	"time"
)

var jwtKey = []byte("secret")

type jwtClaims struct {
	Username string `json:"username"`
	Email string `json:"email"`
	jwt.StandardClaims
}

func GenerateJWT(email string, username string) (tokenString string, err error) {
	expirationTime := time.Now().Add(1 * time.Hour)
	claims:= &jwtClaims{
		Email: email,
		Username: username,
		StandardClaims: jwt.StandardClaims{
			ExpiresAt: expirationTime.Unix(),
		},
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err = token.SignedString(jwtKey)
	return
}

func ValidateTokens(signedToken string) (err error){
	token, err := jwt.ParseWithClaims(
			signedToken,
			&jwtClaims{},
			func(token *jwt.Token) (interface{}, error){
				return []byte(jwtKey), nil
			},
		)
	if err != nil {
		return
	}
	claims, ok := token.Claims.(*jwtClaims)
	if !ok {
		err = errors.New("could not parse claims")
		return
	}
	if claims.ExpiresAt<time.Now().Local().Unix(){
		err = errors.New("token expired")
		return
	}
	return
}