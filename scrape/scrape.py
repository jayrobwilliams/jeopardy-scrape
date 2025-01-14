import sys
import argparse
import pg
import build
import game_links
import game_data

def by_season(conn, cur, links):
    for season in links:
        length = len(links[season])
        for i in range(length):
            jeopardy_data = game_data.get(links[season][i], season)
            amtDone = float(i+1)/float(length)
            if(len(jeopardy_data) > 0):
                new = build.games(cur, jeopardy_data)
                if not new:
                    sys_text = " duplicate... skipping..."
                else:
                    build.contestants(cur, jeopardy_data["contestants"], jeopardy_data["id"])
                    build.rounds(cur, jeopardy_data["rounds"], jeopardy_data["id"])
                    sys_text = " scrape and insert done..."
                pg.commit(conn)
                sys.stdout.write("\rSeason " + str(season) + " Progress: [{0:50s}] {1:.1f}%".format('#' * int(amtDone * 50), amtDone * 100) + " Episode " + jeopardy_data["show_number"] + sys_text)
                sys.stdout.flush()
        sys.stdout.write("\n")

def by_episode(conn, cur, link, season):
    jeopardy_data = game_data.get(link, season)
    new = build.games(cur, jeopardy_data)
    if not new:
        sys_text = " duplicate episode... skipping..."
    else:
        build.contestants(cur, jeopardy_data["contestants"], jeopardy_data["id"])
        build.rounds(cur, jeopardy_data["rounds"], jeopardy_data["id"])
        sys_text = " scrape and insert done..."
    pg.commit(conn)
    sys.stdout.write("\rSeason " + str(season) + " Episode " + jeopardy_data["show_number"] + sys_text)
    sys.stdout.write("\n")

if __name__ == "__main__":
    conn, cur = pg.connect()

    parser = argparse.ArgumentParser(description="Scrape J! Archive")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--episode", nargs=2, metavar=('url', 'season'), help="Only scrape one episode")
    group.add_argument("-s", "--season", nargs=2, metavar=('start_season', 'end_season'), type=int, choices=range(1, 39), help="Scrape specific seasons")
    group.add_argument("-ss", "--season-start", nargs=1, metavar=('start_season'), type=int, choices=range(1, 39), help="Scrape from start season and end at end of show")
    group.add_argument("-a", "--all", action='store_true', help="Scrape all seasons")
    args = parser.parse_args()

    if args.episode:
        by_episode(conn, cur, args.episode[0], args.episode[1])
    else:
        if args.all:
            links = game_links.get()
        elif args.season:
            if args.season[0] > args.season[1]:
                parser.error("First season must be less than last season")
            else:
                links = game_links.get(args.season[0], args.season[1])
        elif args.season_start:
            links = game_links.get(args.season_start[0])
        else:
            parser.error("There's been an error. Oops.")

        by_season(conn, cur, links)

    pg.disconnect(conn, cur)

    print("Data successfully uploaded")
