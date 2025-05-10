import type {
  DataState,
  DataState_Success,
  UseQueryOptions,
  UseQueryReturn,
} from '@pinia/colada'
import { StatusCodes } from 'http-status-codes'

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
    mutate: loginRaw,
    status: loginStatus,
    asyncStatus: loginAsyncStatus,
  } = useLoginMutation()

  const username = ref('')
  const password = ref('')

  const login = async () =>
    loginRaw({
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
      } satisfies DataState_Success<TResult>
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
