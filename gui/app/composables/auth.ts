import type {
  DataState,
  UseQueryOptions,
  UseQueryReturn,
  UseInfiniteQueryOptions,
  UseInfiniteQueryReturn,
} from '@pinia/colada'
import { useInfiniteQuery, useQuery } from '@pinia/colada'
import type { RouteLocationGeneric } from 'vue-router'
import { StatusCodes } from 'http-status-codes'
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

type UseAuthOptions = {
  fallbackRoute?: MaybeRefOrGetter<string | RouteLocationGeneric>
}

export function useAuth(options?: UseAuthOptions) {
  const { $api } = useNuxtApp()
  const route = useRoute()
  const router = useRouter()

  // default options
  options = options ?? {
    fallbackRoute: undefined,
  }

  const { data: me, status: meStatus } = useQuery({
    key: () => ['auth'],
    query: () =>
      $api('/v1/me', {
        onResponse: async (ctx) => {
          if (ctx.response.status === StatusCodes.UNAUTHORIZED) {
            ctx.error = undefined
            ctx.response = new Response('null')
          }
        },
      }),
    refetchOnMount: false,
  })

  // login path
  const loginRoute = computed(() =>
    router.resolve({
      path: '/me/account',
      query: {
        redirect: route.fullPath,
      },
    }),
  )

  const loggedIn = computed(() => unref(meStatus) === 'pending' ? undefined : unref(me) != null)

  // if fallbackRoute is given, navigate to it when logged out
  const stop = watchEffect(() => {
    const _route = toValue(options.fallbackRoute)
    if (_route != null && unref(loggedIn) == false)
      navigateTo(_route)
  })

  tryOnUnmounted(stop)

  return { loggedIn, loginRoute }
}

export function useLogin() {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  const { mutateAsync: login, ...mutation } = useMutation({
    mutation: (ctx: { username: string, password: string }) => {
      // create form data
      const formData = new FormData()
      formData.append('grant_type', 'password')
      formData.append('username', ctx.username)
      formData.append('password', ctx.password)

      return $api('/v1/auth/login', {
        method: 'POST',
        // @ts-expect-error: cannot type FormData
        body: formData,
      })
    },

    onSettled: () => {
      queryCache.invalidateQueries({ key: ['me'] })
      queryCache.invalidateQueries({ key: ['auth'] })
    },

    onSuccess: () => {
      localStorage.setItem('auth-session', 'true')
    },
  })

  return { login, ...mutation }
}

export function useLogout() {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  const { mutateAsync: logout, ...mutation } = useMutation({
    mutation: () => {
      return $api('/v1/auth/logout', {
        method: 'POST',
      })
    },

    onSettled: () => {
      queryCache.invalidateQueries({ key: ['me'] })
      queryCache.invalidateQueries({ key: ['auth'], exact: true })
    },

    onSuccess: () => {
      localStorage.removeItem('auth-session')
    },
  })

  return { logout, ...mutation }
}

export function useQueryWithAuth<
  TResult,
  TError,
  TDataInitial extends TResult | undefined = undefined,
>(
  options: UseQueryOptions<TResult, TError, TDataInitial>,
): UseQueryReturn<TResult, TError, TDataInitial> {
  const { loggedIn } = useAuth()

  const { state, ...queryResult } = useQuery<TResult, TError, TDataInitial>({
    enabled: () => unref(loggedIn) === true,
    ...options,
  })

  const modifiedState = computed<DataState<TResult, TError, TDataInitial>>(
    () => {
      const _state = unref(state)

      if (unref(loggedIn) === true) return _state

      return {
        status: 'success',
        data: undefined as TResult,
        error: null,
      }
    },
  )

  return {
    ...queryResult,
    state: modifiedState,

    status: computed(() => unref(modifiedState).status),
    data: computed(() => unref(modifiedState).data),
    error: computed(() => unref(modifiedState).error),

    isPending: computed(() => unref(modifiedState).status === 'pending'),
  }
}

export function useInfiniteQueryWithAuth<
  TData,
  TError,
  TPage = unknown,
>(
  options: UseInfiniteQueryOptions<TData, TError, TData | undefined, TPage>,
): UseInfiniteQueryReturn<TPage, TError> {
  const { loggedIn } = useAuth()

  const { state, ...queryResult } = useInfiniteQuery<TData, TError, TPage>({
    enabled: () => unref(loggedIn) === true,
    ...options,
  })

  const modifiedState = computed<DataState<TPage, TError, TPage>>(
    () => {
      const _state = unref(state)

      if (unref(loggedIn) === true) return _state

      return {
        status: 'success',
        data: toValue(options.initialPage),
        error: null,
      }
    },
  )

  return {
    ...queryResult,
    state: modifiedState,

    status: computed(() => unref(modifiedState).status),
    data: computed(() => unref(modifiedState).data),
    error: computed(() => unref(modifiedState).error),

    isPending: computed(() => unref(modifiedState).status === 'pending'),
  }
}

export function useAuthPasswordResetValidation(
  email: MaybeRefOrGetter<string>,
  touched?: MaybeRefOrGetter<boolean>,
) {
  const _touched: MaybeRefOrGetter<boolean> = touched === undefined ? true : touched

  // email trimmed and without consecutive whitespaces
  const cleanedEmail = computed(() => avoidConsecutiveWhitespaces(toValue(email).trim()))

  // delayed propagation of the cleaned email
  const { value: throttledEmail, synced: throttledEmailSynced } = useThrottle(cleanedEmail, 500)

  // retrieve user email avAsyncDataRequestStatusailability from API
  const {
    data: emailAvailability,
    status: emailAvailabilityStatus,
    asyncStatus: emailAvailabilityAsyncStatus,
  } = useAuthAccountEmailAvailableQuery(throttledEmail)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _email = unref(cleanedEmail)

    if (_email === '')
      return 'Veuillez spécifier une adresse email'

    if (unref(emailAvailabilityStatus) === 'error')
      return 'Adresse email invalide'

    if (unref(emailAvailability)?.available === true)
      return 'Cette adresse n\'existe pas'

    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(_touched) === false)
      return 'idle'

    if (unref(throttledEmailSynced) === false || unref(emailAvailabilityAsyncStatus) === 'loading')
      return 'pending'

    if (unref(error) != null)
      return 'error'

    return 'success'
  })

  return {
    email: cleanedEmail,
    status,
    error,
  }
}
