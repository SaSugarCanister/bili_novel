class get_text:
    #获取当前章节页的小说正文内容
    def get_chapter_text(self,driver) -> list:
        text_lst = driver.execute_script(
            """
                // 准备一个空数组，用来装过滤后的结果(解决文本投毒)
                var result = [];
                // 先找到要的元素
                var container = document.querySelector('#TextContent');
                // 在这个元素下面找所有 p、br、center、img
                var ps = container.querySelectorAll('p,br,center,img');
                // 循环遍历每个 <p>/<center> 标签
                for (var i = 0; i < ps.length; i++) {
                    // 获取这个 <p> 在屏幕上实际渲染的尺寸和位置
                    var rect = ps[i].getBoundingClientRect();
                    //  判断：宽度大于0 且 高度大于0
                    if (rect.width > 0 || rect.height > 0) {
                        if (ps[i].id === "show-more-images") {
                            result.push("");
                            continue;
                        } 
                        if (ps[i].tagName === 'IMG' || ps[i].tagName === 'BR') {
                            if (ps[i].tagName === 'BR') {
                                result.push(ps[i].outerHTML);
                            } else {
                                result.push(ps[i].getAttribute('src'));
                            }                          
                        } else {
                            result.push(ps[i].innerText);
                        }
                    } else {
                        result.push("")
                    }
                }
                return result
            """
        )

        return text_lst

