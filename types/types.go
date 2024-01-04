package types

import (
	"go.mongodb.org/mongo-driver/bson/primitive"
	"time"
)

type Admin struct {
	ID         primitive.ObjectID `bson:"_id,omitempty"`
	name       string             `bson:"name" validate:"required"`
	email      string             `bson:"email" validate:"required"`
	password   string             `bson:"password" validate:"required"`
	role       string             `bson:"role"`
	schoolName string             `bson:"schoolName"`
}

type Complain struct {
	ID        primitive.ObjectID `bson:"_id,omitempty"`
	User      primitive.ObjectID `bson:"User" validate:"required"`
	Date      time.Time          `bson:"date" validate:"required"`
	Complaint string             `bson:"complaint" validate:"required"`
	School    string             `bson:"school" validate:"required"`
}

type Notice struct {
	Title   string    `bson:"title" validate:"required"`
	Details string    `bson:"details" validate:"required"`
	Date    time.Time `bson:"date" validate:"required"`
	School  string    `bson:"school" validate:"required"`
}

type ClassSchema struct {
	ClassName string `bson:"className" validate:"required"`
	School    string `bson:"school" validate:"required"`
}

type ExamResult struct {
	SubName       primitive.ObjectID `bson:"SubName,omitempty"`
	MarksObtained int                `bson:"MarksObtained,omitempty"`
}

type Attendance struct {
	Date    primitive.ObjectID `bson:"Date,omitempty"`
	Status  string             `bson:"Status,omitempty"`
	SubName primitive.ObjectID `bson:"SubName,omitempty"`
}

type Student struct {
	ID         primitive.ObjectID `bson:"_id,omitempty"`
	Name       string             `bson:"name" validate:"required"`
	RollNum    string             `bson:"rollNum" validate:"required"`
	Password   string             `bson:"password" validate:"required"`
	ClassName  primitive.ObjectID `bson:"className" validate:"required"`
	School     primitive.ObjectID `bson:"school" validate:"required"`
	Role       string             `bson:"role" validate:"required"`
	ExamResult []ExamResult       `bson:"examResult,omitempty"`
	Attendance []Attendance       `bson:"attendance,omitempty"`
}

type Subject struct {
	SubName  string `bson:"SubName" validate:"required"`
	subCode  string `bson:"SubCode" validate:"required"`
	sessions string `bson:"Sessions validate:required"`
}
