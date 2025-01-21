import type { RouterConfig } from '@nuxt/schema';

// ensure NuxtLinks jumps to anchors (hash)
// https://github.com/nuxt/nuxt/issues/14033#issuecomment-1536092133
export default <RouterConfig>{
  scrollBehavior(to, from, savedPosition) {
    to.hash;
    if (to.hash) {

      const element = document.getElementById(to.hash.substring(1))

      if (element)
        element.scrollIntoView({ block: 'center' });

    }
  },
};
