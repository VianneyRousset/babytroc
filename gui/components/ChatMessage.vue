<script setup lang="ts">

import { ChatMessageType } from '#build/types/open-fetch/schemas/api';

const props = defineProps<{
  message: ChatMessage,
}>();

// chat
const { message } = toRefs(props);
const { origin, messageType, text, formattedHour } = useChatMessage(message);

const classes = computed(() => ({
  "me": origin.value === 'me',
  "interlocutor": origin.value === 'interlocutor',
  "system": origin.value === 'system',
}));

// item


</script>

<template>
  <div class="ChatMessage" :class="classes">

    <div class="bubble">
      <div>{{ text }}</div>

      <div v-if="messageType === ChatMessageType.loan_request_created">
        x
      </div>
      <div class="hour">{{ formattedHour }}</div>
    </div>

  </div>


</template>

<style scoped lang="scss">
.ChatMessage {

  --message-large-border-radius: 0.8rem;
  --message-small-border-radius: 0.5rem;

  @include flex-column;
  padding: 0.25rem 0.5rem;
  padding-bottom: calc(0.25rem + 2px);

  .bubble {
    line-height: 1.25;
    max-width: 75%;
    padding: 0.5rem .875rem;
    position: relative;
    word-wrap: break-word;
    padding-bottom: 1.2rem;
  }

  /* system messages */
  &.system {

    .bubble {
      border: 1px solid $neutral-300;
      align-self: center;
      color: $neutral-300;
      border-radius: 0.5rem;

      .hour {
        color: black;
      }
    }
  }

  /* user messages */
  &:not(.system) {

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
    &.me {

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
    &.interlocutor {

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

  .hour {
    position: absolute;
    bottom: 0.15rem;
    right: 0.5rem;
    opacity: 0.3;
    font-size: 0.7rem;
  }

}
</style>
