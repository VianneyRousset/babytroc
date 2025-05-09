# API
- Removed pagination on liked and saved items, would be nice to limit the number of liked and saved items
- No need to split create and insert in client.database and no need to create helpers to create db objects. Could it be done from the Model class ?
- pydantic schematics should be think as interfaces (services-routes, routes, ...)
- Should services and clients return HTTP errors. I don't think so. Generic errors could be interpreted by FastAPI to return the proper HTTP status (e.g. a NotFoundError treated as a 404)
- https://github.com/Kludex/fastapi-tips

## TODO
- check alembic version files for proper indices creation
- check alembic check constraint "loan_request_executed_or_not". Looks wrong
- add test on full loan creation chain
- improve targeted_age_months serialization/deserialization with a new pydantic type

# GUI

## TODO
- change Nuxt file structure to v4

## Extensions to consider
- [NuxtAuth](https://github.com/sidebase/nuxt-auth)
- [Pinia](https://pinia.vuejs.org/introduction.html) - A store
- [VeeValidate](https://vee-validate.logaretm.com/v4/) - Forms
- [FormKit](https://formkit.com/) - Forms
- [Toastification](https://vue-toastification.maronato.dev/) - Notifications
- [Swiper](https://swiperjs.com/element) - Swipe images in galleries
- [VueUse](https://vueuse.org/) - Utilities
