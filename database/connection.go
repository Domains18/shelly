package database

import (
	"github.com/Domains18/ReactGoAuth/models"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

var DB *gorm.DB

func Connect() {
	connection, err := gorm.Open(mysql.Open("root:rootroot@/goauth"), &gorm.Config{})
	if err != nil {
		panic("could not connect to the database")
	}
	DB = connection
	err = connection.AutoMigrate(&models.User{})
	if err != nil {
		return
	}
}
