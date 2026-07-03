import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./assets/main.css";
import "preline/preline";

createApp(App).use(createPinia()).use(router).mount("#app");
