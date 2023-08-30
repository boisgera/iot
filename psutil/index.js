/* Shit, this stuff is async ...*/
function fetch() {
  m.request({ method: "GET", url: "/api" }).then(function (response) {
    window.response = response;
    m.redraw();
    setTimeout(fetch, 1000);
  });
}

window.response = [];
fetch();

function Table() {
  return {
    view: function () {
      console.log(window.response);
      let data = window.response;
      return m(
        "table",
        m("thead", [
          m("tr", [
            m("th", "ID"),
            m("th", "Name"),
            m("th", "Compute (%)"),
            m("th", "Memory (%)"),
          ]),
        ]),
        m(
          "tbody",
          data.map((process) =>
            m("tr", [
              m("td", process.pid),
              m("td", process.name),
              m("td", process.cpu_percent),
              m("td", process.memory_percent),
            ])
          )
        )
      );
    },
  };
}

m.mount(document.getElementById("mithril"), Table);
