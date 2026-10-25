import discord

async def send_embeds(channel, topics):
    for start in range(0, len(topics), 10):
        batch = topics[start:start+10]
        embeds = []
    
        for t in batch:
            embed = discord.Embed(
                    title = t["title"],
                    url = t["url"],
                    description = t["summary"],
                    color = discord.Color.blurple()
                    )
            embed.add_field(
                    name = "サイト名",
                    value = t["name"],
                    inline = True
                    )
            embeds.append(embed)

        if embeds:
            await channel.send(
                    content = f"**新着記事** ({len(embeds)}件)",
                    embeds = embeds
                    )
