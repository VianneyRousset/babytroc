import { cloneVNode, type VNode } from 'vue'

function unwrap(
  vnode: VNode,
): Array<VNode> {
  // no children
  if (vnode.children == null)
    return []

  // @ts-expect-error default is defined in vnode.children
  return vnode.children.default()
}

function bindAttrs(
  vnode: VNode,
  attrs: Record<string, unknown>,
): VNode {
  return cloneVNode(vnode, attrs, true)
}

export default defineComponent({
  name: 'Unwrap',
  inheritAttrs: false,
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, context) {
    return () => (
      props.disabled
        ? context.slots.default?.()?.map(vnode => bindAttrs(vnode, context.attrs))
        : context.slots?.default?.().flatMap(unwrap).map(vnode => bindAttrs(vnode, context.attrs))
    )
  },
})
