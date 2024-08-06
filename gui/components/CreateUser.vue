<script setup lang="ts">
let name = "";
let email = "";
let password = "";

const passwordInput = ref(null);

const emit = defineEmits(["signup"]);

async function signup() {
  try {
    const { token } = await $fetch("/api/users", {
      method: "POST",
      body: { name, email, password },
    });
    emit("signup", token);
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
      <h1>Signup</h1>
      <div class="tooltip-container">
        <span class="tooltip">Try again</span>
        <div style="display: flex; margin-bottom: 1em">
          <input
              id="signup-name"
              v-model="name"
              class="big"
              type="text"
              placeholder="Name"
              @keyup.enter="emailInput.value.focus()"
              autofocus
              />
        </div>
      </div>
      <input
          id="signup-email"
          ref="emailInput"
          v-model="email"
          class="big"
          type="text"
          placeholder="Email"
          @keyup.enter="passwordInput.value.focus()"
          autofocus
          />
      <InputGo
          ref="passwordInput"
          v-model="password"
          placeholder="Password"
          type="password"
          @submit="signup()"
          />
    </div>
  </div>
</template>


<style scoped>
#box {
  color: white;
  display: flex;
  justify-content: center;
  height: 30vh;
  min-height: 40em;
  background: url("/img/signup-email-box.svg") no-repeat center center;
  background-size: 30em;
}

#box > div {
  width: 20em;
  margin-top: 8em;
  margin-right: 1em;
}

h1 {
  font-weight: normal;
  font-size: 2em;
  color: white;
}

p {
  margin-left: 0.5em;
  margin-top: 1.5em;
  color: #e7e7e6ff;
}

@media only screen and (max-width: 800px) {
  #box > div {
    margin-left: 1em;
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
