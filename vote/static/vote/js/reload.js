$(document).ready(() => {
  let timeout;

  function reload() {
    console.log("Reloading")
    //wait a random time, to not overload the server if everyone reloads at the same time
    window.setTimeout(() => $("#content").load(location.pathname + " #content"), Math.random() * 1000)
    setup_date_reload()
  }

  function setup_date_reload() {
    //setup a timer to reload the page if a start or end date of a election passed
    clearTimeout(timeout);
    const now_ms = new Date().getTime();
    const times = $(".time").text().split('|').map(u_time => parseInt(u_time));
    const wait_ms = times.map(time => (time + 5) * 1000 - now_ms).filter(t => t > 0);
    const min_ms = Math.min(...wait_ms);
    if (min_ms < 24 * 60 * 60 * 1000) {
      console.log("Reloading in " + (min_ms / 1000) + "s");
      timeout = setTimeout(reload, min_ms);
    }
  }

  setup_date_reload()
})
