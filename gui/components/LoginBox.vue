<script setup lang="ts">
let email = "";
let password = "";

const passwordInput = ref(null);

const emit = defineEmits(["login"]);

async function login() {
  try {
    const { token } = await $fetch("/api/login", {
      method: "POST",
      body: { email, password },
    });
    emit("login", token);
  } catch (e) {
    console.log(e);
    document.querySelector(".tooltip-container").setAttribute("active", "true");
    document.querySelector("#login-email").value = "";
    document.querySelector("#login-password").value = "";
    document.querySelector("#login-email").focus();
  }
}
</script>

<template>
  <div id="box">
    <div>
      <h1>Login</h1>
      <div class="tooltip-container">
        <span class="tooltip">Try again</span>
        <div style="display: flex; margin-bottom: 1em">
          <input id="login-email" v-model="email" class="big" type="text" placeholder="Email"
            @keyup.enter="passwordInput.value.focus()" autofocus />
        </div>
      </div>
      <InputGo ref="passwordInput" v-model="password" placeholder="Password" type="password" @submit="login()" />
      <a>
        <p>Forgot your password ?</p>
      </a>
    </div>
  </div>
</template>

<style scoped>
#box {
  color: white;
  display: flex;
  justify-content: center;
  height: 50vh;
  min-height: 38em;
  background: url("/img/login-box.svg") no-repeat center center;
  background-size: 38em;
}

#box>div {
  display: flex;
  flex-direction: column;
  margin-left: 0.5em;
  width: 20em;
  margin-top: 7em;
}

h1 {
  font-weight: normal;
  font-size: 2em;
  text-align: center;
  color: white;
  margin-bottom: 1.8em;
}

a {
  margin-top: 0.5em;
}

p {
  float: right;
  margin-right: 1.5em;
  color: #e7e7e6ff;
}

p.login-error {
  color: #6b240c;
  text-align: center;
}

@media only screen and (max-width: 800px) {
  #box>div {
    margin-left: 0em;
  }
}

.tooltip-container {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s;
  border-radius: 12px;
  cursor: pointer;
}

.tooltip {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.3em 0.6em;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s;
  background: #fcf5ed;
  border-radius: 12px;
  color: #df826c;
}

.tooltip::before {
  position: absolute;
  content: "";
  height: 0.6em;
  width: 0.6em;
  bottom: -0.2em;
  left: 50%;
  transform: translate(-50%) rotate(45deg);
  background: #fcf5ed;
}

.tooltip-container[active] .tooltip {
  top: -55%;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
</style>
