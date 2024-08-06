<template>
  <div id="box">
    <div>
      <h1>We need your email</h1>
      <InputGo placeholder="Email" @submit="navigateTo('signup-confirm')" />
      <p>
        It will only used for your account.<br />It won't be used for
        advertising.
      </p>
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
</style>
