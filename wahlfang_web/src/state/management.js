import {atom} from "recoil";

export const isManagerAuthenticated = atom({
    key: 'isManagerAuthenticated',
    default: false,
})

export const toggleAddSession = atom({
    key: 'toggleAddSession',
    default: false,
})
