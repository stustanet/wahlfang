import {loadManagerToken} from "./api/management";
import {loadVoterToken} from "./api";

export const voterWebsocketURL = 'ws://localhost:8000/api/v1/vote/'
export const managementWebsocketURL = 'ws://localhost:8000/api/v1/management/'

export class WahlfangWebsocket {
    constructor(url, isVoter) {
        this.url = url;
        this.isVoter = isVoter;
        this.handlers = {}; // map of table name to callback
    }

    initWs = () => {
        const token = this.isVoter ? loadVoterToken() : loadManagerToken();
        const url = this.url + '?token=' + token.access;
        this.ws = new WebSocket(url);
        this.ws.onopen = this.onopen;
        this.ws.onclose = this.onclose;
        this.ws.onmessage = this.onmessage;
    }
    onopen = () => {
        console.log("WS Connected");
    }
    onclose = () => {
        console.log("WS Disconnected");
        this.initWs();
    }
    register = (table, callback) => {
        this.handlers[table] = callback;
    }
    unregister = (table) => {
        if (this.handlers.hasOwnProperty(table)) {
            delete this.handlers[table];
        }
    }
    onmessage = (evt) => {
        const msg = JSON.parse(evt.data)
        console.log("WS Received message: ", msg);

        if (msg.type === "update" && this.handlers.hasOwnProperty(msg.table)) {
            console.log("received update on table", msg.table)
            this.handlers[msg.table]();
        }
    }
}

export const voterWS = new WahlfangWebsocket(voterWebsocketURL, true);
export const managementWS = new WahlfangWebsocket(managementWebsocketURL, false);
