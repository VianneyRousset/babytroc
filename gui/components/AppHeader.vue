<script setup lang="ts">
const route = useRoute();
console.log(route.path);
</script>

<template>
  <header>
    <img id="header-logo" src="/img/logo2.svg" />
    <nav id="header-nav">
      <ul>
        <li :active="route.path.startsWith('/mystuff')">
          <NuxtLink to="/mystuff">My stuff</NuxtLink>
        </li>
        <li :active="route.path.startsWith('/explore')">
          <NuxtLink active to="/explore">Explore</NuxtLink>
        </li>
        <li :active="route.path.startsWith('/faq')">
          <NuxtLink to="/faq">FAQ</NuxtLink>
        </li>
      </ul>
    </nav>
    <AccountMenu class="account" />
  </header>
</template>

<style scoped>
header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0px 24px;
  border-bottom: 1px solid #E3E3E6;
}

#header-logo {
  height: 2rem;
  margin-right: 2rem;
}

#header-nav {
  flex-grow: 1;
  font-weight: 500;
}

#header-nav ul {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  padding: 0 0.7rem;
  gap: 2rem;
}

#header-nav ul li {
  list-style-type: none;
  text-align: center;
}

#header-nav a {
  white-space: nowrap;
  font-size: 1.2rem;
  text-decoration: none;
  color: var(--neutral-500);
}

#header-nav a:hover {
  color: var(--neutral-700);
}

#header-nav li[active="true"] a {
  color: var(--neutral-950);
}

@media only screen and (max-width: 50rem) {
  header {
    justify-content: center;
    align-items: stretch;
    flex-direction: column;
    padding: 2rem 2rem;
  }

  #header-nav {
    margin-top: 2rem;
  }


  #header-nav ul {
    justify-content: space-between;
  }

  .account {
    position: absolute;
    top: 0px;
    left: 0px;
    visibility: hidden;
  }

  #header-nav ul li {}

  #header-nav a {
    font-size: clamp(0.2rem, 0.2rem + 4vw, 1.8rem);
  }
}
</style>
