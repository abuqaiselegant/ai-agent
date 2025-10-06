import streamlit as st

def render_news(items: list | None):
    if not items:
        st.info("No news.")
        return
    for n in items[:30]:
        with st.container(border=True):
            title = n.get("title","(no title)")
            url = n.get("url")
            source = n.get("source")
            ts = n.get("published_at")
            st.markdown(f"**{title}**")
            meta = " · ".join([x for x in [source, ts] if x])
            if meta:
                st.caption(meta)
            if url:
                st.markdown(f"[Open link]({url})")
            if n.get("summary"):
                with st.expander("Summary"):
                    st.write(n["summary"])
