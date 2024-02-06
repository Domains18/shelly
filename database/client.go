package database;

import (
	"github.com/Domains18/SchoolIt/models"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"log"
)


var Instance *gorm.DB
var dbError error

func Connect(connectionString string)(){
	Instance, dbError = gorm.Open(mysql.Open(connectionString), &gorm.Config{})
	if dbError != nil {
		log.Fatalln(dbError)
	}
	log.Println("database pinged successfully")
}

func Migrate(){
	err := Instance.AutoMigrate(&models.User{})
	if err != nil {
		return
	}
	log.Println("Database Migration Successfully")
}