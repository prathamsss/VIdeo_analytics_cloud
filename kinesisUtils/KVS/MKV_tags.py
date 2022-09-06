import datetime
import re


def getMkvTagVal(chunk, reqs):
    # decoding into english (from binary) to run regex commands on the chunk/metadata
    chunk_en = chunk.decode('cp437')
    tags = []

    try:

        for req in reqs:

            if req == "fragment":

                match = re.search(
                    "AWS_KINESISVIDEO_FRAGMENT_NUMBERD", chunk_en)

                if match:
                    fragment_nbr_chunk = re.split(
                        "AWS_KINESISVIDEO_FRAGMENT_NUMBERD", chunk_en)
                val = fragment_nbr_chunk[1]
                val = val[val.find("ç") + 1:val.find("g")]
                res = []
                for x in val:

                    if x.isdigit() or x == ".":
                        res.append(x)
                tags.append("".join(res))

            if req == "server_timestamp":
                match1 = re.search(
                    "AWS_KINESISVIDEO_SERVER_TIMESTAMPD", chunk_en)

                if match1:
                    server_time_chunk = re.split(
                        "AWS_KINESISVIDEO_SERVER_TIMESTAMPD", chunk_en)

                nextval = server_time_chunk[1]
                nextval = nextval[nextval.find("ç") + 1:nextval.find("g")]
                res = []

                for x in nextval:
                    if x.isdigit() or x == ".":
                        res.append(x)

                res = datetime.datetime.utcfromtimestamp(
                    float("".join(res))).isoformat()
                tags.append(res)

            if req == "producer_timestamp":
                match2 = re.search(

                    "AWS_KINESISVIDEO_PRODUCER_TIMESTAMPD", chunk_en)
                if match2:
                    producer_time_chunk = re.split(

                        "AWS_KINESISVIDEO_PRODUCER_TIMESTAMPD", chunk_en)

                nextval2 = producer_time_chunk[1]
                nextval2 = nextval2[nextval2.find("ç") + 1:nextval2.find("g")]

                res = []

                for x in nextval2:
                    if x.isdigit() or x == ".":
                        res.append(x)

                #sec_res = []
                my_sec_res = res[:res.index('.')]
                mili_sec = res[res.index('.'):]
                new_ms = []

                for ms in mili_sec:
                    if ms =="." or ms == '²':
                        pass
                    elif ms.isdigit():
                        new_ms.append(ms)
                new_ms.insert(0, ".")

                sec_res = my_sec_res + new_ms

                # for index, char in enumerate(res):
                #
                #     if char == ".":
                #
                #         sec_res.append(char)
                #
                #         for milisec in res[res.index(char) + 1:]:
                #
                #             if milisec == "." or milisec == "²":
                #                 break
                #
                #             sec_res.append(milisec)
                #
                #         break
                #
                #     sec_res.append(char)
                # print("original final ==>",sec_res)

                res = datetime.datetime.utcfromtimestamp(
                    float("".join(sec_res))).isoformat()+'Z'
                tags.append("".join(res))
            print(tags)
            return tags

    except:

        raise ValueError("Tags not found")
