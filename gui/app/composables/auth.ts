import type {
  DataState,
  UseQueryOptions,
  UseQueryReturn,
  UseInfiniteQueryOptions,
  UseInfiniteQueryReturn,
} from '@pinia/colada'
import { useInfiniteQuery, useQuery } from '@pinia/colada'
import { StatusCodes } from 'http-status-codes'
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

export function useAuth() {
  const { $api } = useNuxtApp()
  const route = useRoute()
  const router = useRouter()

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
  })

  // login
  const {
    mutateAsync: loginRaw,
    status: loginStatus,
    asyncStatus: loginAsyncStatus,
  } = useLoginMutation()

  const username = ref('')
  const password = ref('')

  const login = async () => await loginRaw({
    username: unref(username),
    password: unref(password),
  })

  // logout
  const {
    mutate: logout,
    status: logoutStatus,
    asyncStatus: logoutAsyncStatus,
  } = useLogoutMutation()

  // login path
  const loginRoute = computed(() =>
    router.resolve({
      path: '/me/account',
      query: {
        redirect: route.fullPath,
      },
    }),
  )

  return {
    loginRoute,
    username,
    password,
    login,
    loginStatus,
    loginAsyncStatus,
    logout,
    logoutStatus,
    logoutAsyncStatus,
    loggedIn: computed(() => {
      if (unref(meStatus) === 'pending') return undefined
      return unref(me) != null
    }),
    loggedInStatus: meStatus,
  }
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
