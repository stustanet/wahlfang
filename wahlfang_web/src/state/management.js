import {atom, selector, selectorFamily, atomFamily} from "recoil";
import {fetchElections, fetchSessionParticipants, fetchSessions} from "../api/management";
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
});



export const sessionParticipants = atomFamily({
    key: "sessionParticipants",
    default: selectorFamily({
        key: "sessionParticipants/default",
        get: (sessionId) => async ({get}) => {
        return fetchSessionParticipants(sessionId)
    }
    })
})


export const electionsListManager = atom ({
    key: "electionsListManager",
    default: selector({
        key: "electionsListManager/default",
        get: async ({get}) => {
            return await fetchElections();
        }
    })
})


export const electionsManagerBySessionId = selectorFamily({
    key: 'electionsManagerBySessionId',
    get: sessionId => async ({get}) => {
        const elections = await get(electionsListManager);
        return elections.filter(election => election.session === sessionId)
    }
});


