import { createSlice, nanoid } from "@reduxjs/toolkit";


const innitialState = {
    todos: [],
    innitialState,
    reducers: {
        addTodo: (state, action) => {
            const todo = {
                id: nanoid(),
                text: action.payload.text,
                completed: false
            }
            state.todos.push(todo)
        },
        deleteTodo: (state, action) => {
            const id = action.payload.id
            state.todos = state.todos.filter(todo => todo.id !== id)
        }
        
    }
}


export const { addTodo, deleteTodo } = todoSlice.actions
export default todoSlice.reducer
