import {atom, selector, selectorFamily} from "recoil";
import {fetchSessions} from "../api/management";
import {managementWS} from "../websocket";
import {electionList} from "./index";


export const isManagerAuthenticated = atom({
    key: 'isManagerAuthenticated',
    default: false,
})


export const sessionList = atom ({
    key: "sessionList",
    default: selector({
        key: "sessionList/default",
        get: async ({get}) => {
            return await fetchSessions();
        }
    }),
    effects_UNSTABLE: [
        ({setSelf, trigger}) => {
            managementWS.register("session", () => {
                fetchSessions()
                    .then(result => {
                        setSelf(result);
                    })
            })
        },
    ]
})


export const sessionById = selectorFamily({
    key: "sessionById",
    get: (sessionId) => async ({get}) => {
        const sessions = await get(sessionList);
        return sessions.find(session => session.id === sessionId)
    }
})