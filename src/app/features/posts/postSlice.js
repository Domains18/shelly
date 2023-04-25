import { createSlice } from "@reduxjs/toolkit";


const initialState = [
    { id: '1', title: 'learning redux', content: 'It is practically hard' },
    { id: '2', title: "doing react", content: "The more I wann do it, I wanna react" }
];

const postsSlice = createSlice({
    name: 'posts',
    initialState,
    reducers: {}
});

export default postsSlice.reducer;
