import {loadToken} from "./api";

export const wsURL = 'ws://localhost:8000/api/v1/vote/'

export class WahlfangWebsocket {
    constructor(url) {
        this.url = url;
        this.handlers = {}; // map of table name to callback
    }

    initWs = () => {
        const token = loadToken();
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

export const ws = new WahlfangWebsocket(wsURL)