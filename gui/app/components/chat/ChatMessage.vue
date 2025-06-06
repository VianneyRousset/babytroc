<script setup lang="ts">
import { Check, CheckCheck } from 'lucide-vue-next'

const props = defineProps<{
  me: User
  msg: ChatMessage
}>()

const { me, msg } = toRefs(props)

const slots = useSlots()

const { origin } = useChatMessageOrigin(msg, me)
const { isNew } = useChatMessageIsNew(msg, me)
const { $api } = useNuxtApp()

let seeMessageTimeout: ReturnType<typeof setTimeout> | undefined = undefined

watch(isNew, (isNew) => {
  if (isNew === true) {
    seeMessageTimeout = setTimeout(async () => {
      const _msg = unref(msg)
      await $api('/v1/me/chats/{chat_id}/messages/{message_id}/see', {
        method: 'post',
        path: {
          chat_id: _msg.chat_id,
          message_id: _msg.id,
        },
      })
    }, 2000)
  }
}, { immediate: true })

onUnmounted(() => {
  if (seeMessageTimeout !== undefined) {
    clearTimeout(seeMessageTimeout)
    seeMessageTimeout = undefined
  }
})

const { formattedHour } = useChatMessageTime(msg)
</script>

<template>
  <div
    class="ChatMessage"
    :origin="origin"
    :new="isNew"
  >
    <transition
      :name="isNew ? 'pop' : undefined"
      mode="in-out"
      appear
    >
      <div class="bubble">
        <div class="text">
          <slot />
        </div>
        <div
          v-if="slots.buttons"
          class="buttons"
        >
          <slot name="buttons" />
        </div>
        <div class="hour-and-check">
          <div class="hour">
            {{ formattedHour }}
          </div>
          <transition
            name="pop"
            mode="in-out"
          >
            <CheckCheck
              v-if="msg.seen"
              :size="16"
              :stroke-width="1.33"
            />
            <Check
              v-else
              :size="16"
              :stroke-width="1.33"
            />
          </transition>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped lang="scss">
.ChatMessage {

  --message-large-border-radius: 0.8rem;
  --message-small-border-radius: 0.5rem;

  @include flex-column;
  padding: 0.25rem 0.8rem;
  padding-bottom: calc(0.25rem + 2px);

  .bubble {
    @include flex-column;
    align-items: stretch;
    gap: 1rem;

    line-height: 1.25;
    max-width: 85%;
    min-width: 5rem;
    padding: 0.8rem 1rem;
    position: relative;
    word-wrap: break-word;
    padding-bottom: 1.2rem;

    /* text */
    :deep(.text) {
      @include flex-row;
      gap: 0.7rem;

      svg {
        flex-shrink: 0;
      }

    }

    :deep(.buttons) {
      @include flex-row;
      gap: 1rem;

      &>* {
        flex: 1;
      }
    }

  }

  /* system messages */
  &[origin="system"] {

    .bubble {
      border: 1px solid $neutral-400;
      align-self: center;
      color: $neutral-400;
      border-radius: 0.5rem;
      width: 70%;
    }
  }

  /* user messages */
  &[origin="me"],
  &[origin="interlocutor"] {

    .bubble {
      border-radius: var(--message-large-border-radius);
      filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.2));
      position: relative;
      box-sizing: border-box;
    }

    &:last-child {
      .bubble::after {
        content: ' ';
        width: 8px;
        height: 8px;
        border-radius: 50%;
        position: absolute;
        bottom: 0px;
      }
    }

    /* me */
    &[origin="me"] {

      .bubble {
        align-self: flex-end;
        background: $primary-100;
        color: $primary-800;
      }

      /* smaller border radius for siblings messages */
      &:has(~ div) {
        .bubble {
          border-bottom-right-radius: var(--message-small-border-radius)
        }
      }

      &:not(:first-child) {
        .bubble {
          border-top-right-radius: var(--message-small-border-radius)
        }
      }

      &:last-child {
        .bubble {
          border-bottom-right-radius: 0;

          &::after {
            background: $primary-100;
            right: -4px;
          }
        }
      }
    }

    /* interlocutor */
    &[origin="interlocutor"] {

      .bubble {
        align-self: flex-start;
        background: $neutral-100;
        color: $neutral-900;
      }

      /* smaller border radius for siblings messages */
      &:has(~ div) {
        .bubble {
          border-bottom-left-radius: var(--message-small-border-radius)
        }
      }

      &:not(:first-child) {
        .bubble {
          border-top-left-radius: var(--message-small-border-radius)
        }
      }

      &:last-child {
        .bubble {
          border-bottom-left-radius: 0;

          &::after {
            background: $neutral-100;
            left: -4px;
          }
        }
      }
    }
  }

  .hour-and-check {
    @include flex-row;
    color: $neutral-400;
    gap: 0.3rem;
    position: absolute;
    bottom: 0.15rem;
    right: 0.5rem;
    font-size: 0.7rem;
    white-space: nowrap;
  }
}
</style>
