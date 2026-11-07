(() => {
  "use strict";

  // textContent: the value is application text, never markup.
  const paint = (state, payload) => {
    const value = payload.value ?? "—";
    state.value.textContent = value;
    state.value.title = value;
  };

  window.Dachshund.widget("stat", {
    mount(card, payload) {
      const container = card.querySelector(".card-content");
      container.classList.add("stat");

      const value = document.createElement("span");
      value.className = "stat-value";
      container.append(value);

      const state = { value };
      paint(state, payload);

      return state;
    },
    replace: paint,
  });
})();
