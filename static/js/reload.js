$(document).ready(() => {
  let timeout;

  function reload_callback() {
    setup_date_reload();
  }

  function reload(reload_id="#content") {
    console.log("Reloading " + reload_id)
    $(reload_id).load(location.pathname + " " + reload_id, reload_callback)
  }

  function setup_date_reload() {
    //setup a timer to reload the page if a start or end date of a election passed
    clearTimeout(timeout);
    const now_ms = new Date().getTime();
    const times = $(".time").text().split('|').map(u_time => parseInt(u_time));
    const wait_ms = times.map(time => (time + 1) * 1000 - now_ms).filter(t => t > 1000);
    const min_ms = Math.min(...wait_ms);
    if (min_ms < 24 * 60 * 60 * 1000) {
      console.log("Reloading in " + (min_ms / 1000) + "s");
      timeout = setTimeout(reload.bind(this, '#electionCard'), min_ms);
    }
  }

  function setup_websocket() {
    const ws = new WebSocket(location.href.replace("http", "ws"));
    ws.onmessage = function (e) {
      const message = JSON.parse(e.data)
      if (message.reload) {
        reload(message.reload);
      }else if (message.alert){
        if (message.alert.reload)
          // we want to reload the voters because the list might be outdated due to the deletion of
          // voters (optional idea: mark the invalid voters red)
          reload(message.alert.reload);
        $('#alertModalBody').find('p').html(message.alert.msg);
        $('#alertModalTitle').html(message.alert.title);
        $('#alertModal').modal('show');
      }else if (message.succ){
        let succ_div = $('#message-success');
        succ_div.find('div').html(message.succ);
        succ_div.toggleClass('hide');
      }
    }
    ws.onopen = function (e) {
      console.log("Websocket connected");
    }
    ws.onerror = function (e) {
      console.error("Websocket ERROR. Site will not reload automatically");
    }
    ws.onclose = function (e) {
      console.error("Websocket Closed. Site will not reload automatically");
    }
  }
  //$('#alertModal').on('hidden.bs.modal', function (e) {
  //  reload();
  //});
  setup_date_reload();
  setup_websocket();
})
