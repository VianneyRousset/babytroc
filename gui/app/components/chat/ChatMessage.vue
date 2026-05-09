<script setup lang="ts">
const props = defineProps<{
	me: UserPrivate;
	message: ChatMessage;
}>();

const { me, message } = toRefs(props);

const _slots = useSlots();

const { origin } = useChatMessageOrigin(message, me);

// mark message as seen when component is visible for a while
const component = useTemplateRef<HTMLElement>("chat-message");
const { hot } = useChatMessageSeen(message, me, { monitor: component });

const { formattedHour } = useChatMessageTime(message);
</script>

<template>
  <div
    ref="chat-message"
    class="ChatMessage"
    :origin="origin"
    :hot="hot"
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
            v-if="message.seen"
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
  </div>
</template>

<style scoped lang="scss">
.ChatMessage {
  --message-large-border-radius: 16px;
  --message-small-border-radius: 4px;

  @include flex-column;
  padding: $space-1 $space-4;
  padding-bottom: calc(#{$space-1} + 2px);

  .bubble {
    @include flex-column;
    align-items: stretch;
    gap: $space-4;

    line-height: 1.35;
    max-width: 85%;
    min-width: 5rem;
    padding: $space-3 $space-4;
    position: relative;
    word-wrap: break-word;
    padding-bottom: $space-5;
    font-size: 0.95rem;

    :deep(.text) {
      @include flex-row;
      gap: $space-3;
      white-space: preserve wrap;

      svg {
        flex-shrink: 0;
      }
    }

    :deep(.buttons) {
      @include flex-row;
      gap: $space-4;

      & > * {
        flex: 1;
      }
    }
  }

  /* system messages */
  &[origin="system"] {
    .bubble {
      border: 1px solid $neutral-300;
      align-self: center;
      color: $text-primary;
      border-radius: $radius-sm;
      width: 70%;

      .hour-and-check {
        color: $text-tertiary;
      }
    }
  }

  /* user messages */
  &[origin="me"],
  &[origin="interlocutor"] {
    .bubble {
      border-radius: var(--message-large-border-radius);
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
        background: $bg-bubble-me;
        color: white;

        .hour-and-check {
          color: rgba(255, 255, 255, 0.7);
        }
      }

      &:has(~ div) {
        .bubble {
          border-bottom-right-radius: var(--message-small-border-radius);
        }
      }

      &:not(:first-child) {
        .bubble {
          border-top-right-radius: var(--message-small-border-radius);
        }
      }

      &:last-child {
        .bubble {
          border-bottom-right-radius: 0;
          &::after {
            background: $bg-bubble-me;
            right: -4px;
          }
        }
      }
    }

    /* interlocutor */
    &[origin="interlocutor"] {
      .bubble {
        align-self: flex-start;
        background: $bg-bubble-theirs;
        color: $text-primary;
      }

      &:has(~ div) {
        .bubble {
          border-bottom-left-radius: var(--message-small-border-radius);
        }
      }

      &:not(:first-child) {
        .bubble {
          border-top-left-radius: var(--message-small-border-radius);
        }
      }

      &:last-child {
        .bubble {
          border-bottom-left-radius: 0;
          &::after {
            background: $bg-bubble-theirs;
            left: -4px;
          }
        }
      }
    }
  }

  .hour-and-check {
    @include flex-row;
    color: $text-tertiary;
    gap: $space-1;
    position: absolute;
    bottom: $space-1;
    right: $space-2;
    font-size: 0.7rem;
    white-space: nowrap;
  }
}
</style>
