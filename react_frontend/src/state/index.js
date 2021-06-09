import {atom, selector, selectorFamily} from "recoil";
import {fetchElections, fetchVoterInfo} from "../api";
import {ws} from "../websocket";

// mutable state counter to reset the full recoil state after e.g. a logout
export const stateCounter = {
    counter: 0
};

export const isAuthenticated = atom({
    key: 'isAuthenticated',
    default: false,
})

export const voterInfo = atom({
    key: "voterInfo",
    default: selector({
        key: "voterInfo/default",
        get: async ({get}) => {
            return await fetchVoterInfo();
        }
    }),
    effects_UNSTABLE: [
        ({setSelf, trigger}) => {
            ws.register("session", () => {
                fetchVoterInfo()
                    .then(result => {
                        setSelf(result);
                    })
            })
        },
    ]
})

export const electionList = atom({
    key: "electionList",
    default: selector({
        key: "electionList/default",
        get: async ({get}) => {
            return await fetchElections();
        }
    }),
    effects_UNSTABLE: [
        ({setSelf, trigger}) => {
            ws.register("election", () => {
                fetchElections()
                    .then(result => {
                        setSelf(result);
                    })
            })
        },
    ]
})

export const electionById = selectorFamily({
    key: "electionById",
    get: (electionId) => async ({get}) => {
        const elections = await get(electionList);
        return elections.find(election => election.id === electionId);
    }
})

export const openElections = selector({
    key: "openElections",
    get: async ({get}) => {
        const elections = await get(electionList);
        return elections.filter((election) => election.start_date !== null && new Date(election.start_date) <= new Date() && (election.end_date === null || new Date(election.end_date) > new Date()));
    }
})

export const upcomingElections = selector({
    key: "upcomingElections",
    get: async ({get}) => {
        const elections = await get(electionList);
        return elections.filter((election) => election.start_date === null || new Date(election.start_date) > new Date());
    }
})

export const closedElections = selector({
    key: "closedElections",
    get: async ({get}) => {
        const elections = await get(electionList);
        return elections.filter((election) => election.end_date && new Date(election.end_date) <= new Date());
    }
})

export const unpublishedElections = selector({
    key: "unpublishedElections",
    get: async ({get}) => {
        const elections = await get(closedElections);
        return elections.filter((election) => election.result_published === '0');
    }
})

export const publishedElections = selector({
    key: "publishedElections",
    get: async ({get}) => {
        const elections = await get(closedElections);
        return elections.filter((election) => election.result_published === '1');
    }
})
