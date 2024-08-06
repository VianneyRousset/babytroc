<template>
  <div id="box">
    <div>
      <h1>Create an account</h1>
      <InputGo placeholder="Name" @submit="navigateTo('signup-email')" />
      <NuxtLink to="/login">Already have an account ?</NuxtLink>
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
  background: url("/img/signup-name-box.svg") no-repeat center center;
  background-size: 40em;
}

#box > div {
  width: 20em;
  margin-top: 16em;
  margin-left: 6em;
}

h1 {
  font-weight: normal;
  font-size: 2em;
  color: white;
}

a {
  float: right;
  margin-top: 1em;
  cursor: pointer;
}

a:active {
  color: #6e9eb6;
}

@media only screen and (max-width: 800px) {
  #box > div {
    margin-top: 12em;
    margin-left: 2em;
  }
}
</style>
