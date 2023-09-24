import { configureStore } from "@reduxjs/toolkit";
import todoReducer from "../features/Todo/todoslice";


export default configureStore({
    reducer: todoReducer
})
